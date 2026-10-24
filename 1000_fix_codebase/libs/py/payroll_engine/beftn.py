"""libs/py/payroll_engine/beftn.py — INT-005: BEFTN batch file generator.

Generates standard 128-byte fixed-width ASCII batch files according to
Bangladesh Bank Electronic Funds Transfer Network (BEFTN) specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

MAX_ENTRY_PAISA = 10**10 - 1  # entry amount field: 10 digits of paisa
MAX_TOTAL_PAISA = 10**12 - 1  # batch/file total-credit fields: 12 digits of paisa


@dataclass
class BeftnEntry:
    employee_id: str
    employee_name: str
    routing_number: str  # 9-digit BD routing number
    account_number: str
    amount_bdt: Decimal


@dataclass
class BeftnBatchHeader:
    company_name: str
    company_id: str
    originating_routing: str  # 9-digit
    batch_number: int
    settlement_date: date
    description: str = "SALARY"


def format_field(val: str, length: int, align: str = "left", pad_char: str = " ") -> str:
    """Format string or number to fixed width ASCII."""
    val_str = str(val)[:length]
    # A non-ASCII (e.g. Bengali) or control character would break the
    # 128-byte record layout (multi-byte on encode, or a stray CR/LF record).
    if not (val_str.isascii() and val_str.isprintable()):
        raise ValueError(f"BEFTN fields must be printable ASCII: {val_str!r}")
    if align == "right":
        return val_str.rjust(length, pad_char)
    return val_str.ljust(length, pad_char)


def validate_routing_number(routing: str) -> bool:
    """Validates 9-digit routing number format (ASCII digits 0-9 only)."""
    return len(routing) == 9 and routing.isascii() and routing.isdigit()


def generate_beftn_batch_file(
    header: BeftnBatchHeader, entries: list[BeftnEntry], created_at: datetime | None = None
) -> str:
    """Produces the complete 128-byte line BEFTN file."""
    if not validate_routing_number(header.originating_routing):
        raise ValueError(f"Invalid originating routing number: {header.originating_routing}")
    if not entries:
        raise ValueError("Cannot generate BEFTN file with empty entries list")

    now = created_at or datetime.now()
    creation_date = now.strftime("%y%m%d")
    creation_time = now.strftime("%H%M")
    eff_date = header.settlement_date.strftime("%y%m%d")

    lines: list[str] = []

    # 1. File Header (Type 1) - 128 bytes
    # Pos: 1(1), 2-3(Priority=01), 4-13(Dest Routing), 14-23(Origin Routing), 24-29(Date), 30-33(Time), 34(File Mod=A), 35-37(128), 38-39(10), 40(1), 41-63(Dest Name), 64-86(Orig Name), 87-94(Ref)
    f_header = (
        "1"
        + "01"
        + format_field("BBANK     ", 10)
        + format_field(header.originating_routing, 10)
        + creation_date
        + creation_time
        + "A"
        + "128"
        + "10"
        + "1"
        + format_field("BANGLADESH BANK", 23)
        + format_field(header.company_name, 23)
        + format_field("SALARY", 8)
        + " " * 34
    )
    lines.append(f_header[:128])

    # 2. Batch Header (Type 5) - 128 bytes
    # Pos: 1(5), 2-4(220=Credit Only), 5-20(Company Name), 21-40(Disc Data), 41-50(Company ID), 51-53(PPD), 54-63(Desc), 64-69(Date), 70-75(Eff Date), 76-78(Settlement), 79(1), 80-87(DFI ID), 88-94(Batch No)
    b_header = (
        "5"
        + "220"
        + format_field(header.company_name, 16)
        + " " * 20
        + format_field(header.company_id, 10)
        + "PPD"
        + format_field(header.description, 10)
        + creation_date
        + eff_date
        + "   "
        + "1"
        + header.originating_routing[:8]
        + format_field(str(header.batch_number), 7, align="right", pad_char="0")
        + " " * 34
    )
    lines.append(b_header[:128])

    # 3. Entry Detail Records (Type 6) - 128 bytes
    entry_hash_sum = 0
    total_credit_paisa = 0

    for idx, entry in enumerate(entries, start=1):
        if not validate_routing_number(entry.routing_number):
            raise ValueError(
                f"Invalid beneficiary routing number: {entry.routing_number} for {entry.employee_id}"
            )
        if entry.amount_bdt <= 0:
            raise ValueError(f"Amount must be positive: {entry.amount_bdt} for {entry.employee_id}")

        routing_8 = entry.routing_number[:8]
        check_digit = entry.routing_number[8]
        entry_hash_sum += int(routing_8)

        # Convert amount to Paisa (1 BDT = 100 Paisa) - exact, never rounded
        scaled = entry.amount_bdt * Decimal("100")
        if scaled != scaled.to_integral_value():
            raise ValueError(
                f"Amount must be a whole number of paisa: {entry.amount_bdt} for {entry.employee_id}"
            )
        paisa = int(scaled)
        if paisa > MAX_ENTRY_PAISA:
            raise ValueError(
                f"Amount exceeds the 10-digit BEFTN amount field: {entry.amount_bdt} "
                f"for {entry.employee_id}"
            )
        total_credit_paisa += paisa

        trace_num = f"{header.originating_routing[:8]}{idx:07d}"

        e_line = (
            "6"
            + "22"  # Demand Credit
            + routing_8
            + check_digit
            + format_field(entry.account_number, 17)
            + format_field(str(paisa), 10, align="right", pad_char="0")
            + format_field(entry.employee_id, 15)
            + format_field(entry.employee_name, 22)
            + "  "
            + "0"
            + format_field(trace_num, 15)
            + " " * 34
        )
        lines.append(e_line[:128])

    if total_credit_paisa > MAX_TOTAL_PAISA:
        raise ValueError(
            f"Batch total exceeds the 12-digit BEFTN total field: {total_credit_paisa} paisa"
        )

    # 4. Batch Control (Type 8) - 128 bytes
    entry_count = len(entries)
    hash_str = str(entry_hash_sum)[-10:].rjust(10, "0")
    b_control = (
        "8"
        + "220"
        + format_field(str(entry_count), 6, align="right", pad_char="0")
        + hash_str
        + "0" * 12  # Total Debit
        + format_field(str(total_credit_paisa), 12, align="right", pad_char="0")
        + format_field(header.company_id, 10)
        + " " * 19
        + " " * 6
        + header.originating_routing[:8]
        + format_field(str(header.batch_number), 7, align="right", pad_char="0")
        + " " * 34
    )
    lines.append(b_control[:128])

    # 5. File Control (Type 9) - 128 bytes
    f_control = (
        "9"
        + "000001"  # 1 Batch
        + format_field(
            str((len(lines) + 1 + 9) // 10), 6, align="right", pad_char="0"
        )  # Block Count
        + format_field(str(entry_count), 8, align="right", pad_char="0")
        + hash_str
        + "0" * 12  # Total Debit
        + format_field(str(total_credit_paisa), 12, align="right", pad_char="0")
        + " " * 39
        + " " * 34
    )
    lines.append(f_control[:128])

    return "\r\n".join(lines) + "\r\n"
