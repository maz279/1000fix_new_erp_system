"""libs/py/payroll_engine - BEFTN (INT-005) calendar and 128-byte file tests.

Pins the Bangladesh Bank clearing calendar (Sunday-Thursday week, 16:00
final cut-off, fixed public holidays, roll-forward) and the fixed-width
batch file layout byte by byte (file header 1, batch header 5, entry
detail 6, batch control 8, file control 9), the routing-number validation
and every rejection path - including the regression tests for defects
fixed in beftn.py (non-ASCII digits accepted as routing numbers,
silently truncated / rounded amounts, non-ASCII or control characters in
text fields breaking the 128-byte layout).
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]

_ROOT = Path(__file__).resolve().parents[4]  # codebase root (libs.py.*)
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from libs.py import payroll_engine as pe
from libs.py.payroll_engine import beftn

D = Decimal
CREATED = datetime(2026, 10, 1, 11, 5)
ORIGIN = "125272345"


def _header(**overrides: object) -> beftn.BeftnBatchHeader:
    fields: dict[str, object] = {
        "company_name": "1000 FIX SERVICES",
        "company_id": "COMP001",
        "originating_routing": ORIGIN,
        "batch_number": 42,
        "settlement_date": date(2026, 10, 4),
        "description": "SALARY",
    }
    fields.update(overrides)
    return beftn.BeftnBatchHeader(**fields)  # type: ignore[arg-type]


def _entry(**overrides: object) -> beftn.BeftnEntry:
    fields: dict[str, object] = {
        "employee_id": "EMP-001",
        "employee_name": "RAHIM UDDIN",
        "routing_number": "085261234",
        "account_number": "1051234567890",
        "amount_bdt": D("45000.50"),
    }
    fields.update(overrides)
    return beftn.BeftnEntry(**fields)  # type: ignore[arg-type]


def _two_entries() -> list[beftn.BeftnEntry]:
    return [
        _entry(),
        _entry(
            employee_id="EMP-002",
            employee_name="FATIMA BEGUM",
            routing_number="095271234",
            account_number="2059876543210",
            amount_bdt=D("52000.00"),
        ),
    ]


def _lines(content: str) -> list[str]:
    assert content.endswith("\r\n")
    return content[:-2].split("\r\n")


# ---------------------------------------------------------------------------
# Clearing calendar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("day", "working"),
    [
        (date(2026, 10, 4), True),  # Sunday
        (date(2026, 10, 5), True),  # Monday
        (date(2026, 10, 8), True),  # Thursday
        (date(2026, 10, 2), False),  # Friday
        (date(2026, 10, 3), False),  # Saturday
    ],
)
def test_sunday_to_thursday_clearing_week(day: date, working: bool) -> None:
    assert pe.is_working_day(day) is working


@pytest.mark.parametrize(("month", "day"), sorted(pe.FIXED_HOLIDAYS))
def test_fixed_public_holidays_are_never_clearing_days(month: int, day: int) -> None:
    for year in (2026, 2027, 2028):
        assert pe.is_working_day(date(year, month, day)) is False


def test_fixed_holiday_set_and_weekend() -> None:
    holidays, weekend = pe.FIXED_HOLIDAYS, pe.WEEKEND
    assert holidays == {(2, 21), (3, 26), (4, 14), (5, 1), (8, 15), (12, 16), (12, 25)}
    assert weekend == {4, 5}  # Friday, Saturday (Monday = 0)


def test_extra_holidays_only_block_listed_days() -> None:
    eid = {date(2026, 10, 6)}
    assert pe.is_working_day(date(2026, 10, 6), eid) is False
    assert pe.is_working_day(date(2026, 10, 7), eid) is True
    assert pe.is_working_day(date(2026, 10, 6), set()) is True
    assert pe.is_working_day(date(2026, 10, 6), None) is True


@pytest.mark.parametrize(
    ("submitted", "settles"),
    [
        (datetime(2026, 10, 1, 10, 0), date(2026, 10, 1)),  # Thu before cut-off
        (datetime(2026, 10, 1, 15, 59), date(2026, 10, 1)),  # last minute in time
        (datetime(2026, 10, 1, 16, 0), date(2026, 10, 4)),  # 16:00 is past cut-off -> Sun
        (datetime(2026, 9, 30, 17, 0), date(2026, 10, 1)),  # Wed late -> Thu
        (datetime(2026, 10, 2, 10, 0), date(2026, 10, 4)),  # Friday -> Sunday
        (datetime(2026, 10, 3, 11, 0), date(2026, 10, 4)),  # Saturday -> Sunday
        (datetime(2026, 3, 25, 17, 0), date(2026, 3, 29)),  # -> Independence Day Thu -> Sun
        (datetime(2026, 4, 13, 16, 30), date(2026, 4, 15)),  # -> Pohela Boishakh -> Wed
        (datetime(2026, 12, 16, 9, 0), date(2026, 12, 17)),  # Victory Day -> Thu
        (datetime(2026, 12, 24, 17, 0), date(2026, 12, 27)),  # -> Christmas Fri -> Sun
    ],
)
def test_beftn_settlement_date_rolls_forward(submitted: datetime, settles: date) -> None:
    assert pe.beftn_settlement_date(submitted) == settles


def test_custom_cutoff_hour() -> None:
    assert pe.beftn_settlement_date(datetime(2026, 10, 5, 14, 30), cutoff_hour=14) == date(
        2026, 10, 6
    )
    assert pe.beftn_settlement_date(datetime(2026, 10, 5, 13, 59), cutoff_hour=14) == date(
        2026, 10, 5
    )


def test_extra_holiday_run_rolls_past_the_weekend() -> None:
    eid = {date(2026, 10, 6), date(2026, 10, 7), date(2026, 10, 8)}
    assert pe.beftn_settlement_date(datetime(2026, 10, 6, 9, 0), extra_holidays=eid) == date(
        2026, 10, 11
    )


# ---------------------------------------------------------------------------
# Routing number validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("routing", "valid"),
    [
        ("125272345", True),
        ("000000000", True),
        ("12527234", False),  # 8 digits
        ("1252723450", False),  # 10 digits
        ("12527234A", False),
        ("12527 345", False),
        ("", False),
    ],
)
def test_validate_routing_number(routing: str, valid: bool) -> None:
    assert pe.validate_routing_number(routing) is valid
    assert beftn.validate_routing_number is pe.validate_routing_number


@pytest.mark.parametrize(
    "routing",
    [
        "০৮৫২৬১২৩৪",  # Bengali digits
        "１２５２７２３４５",  # full-width digits
        "12527234²",  # superscript two
    ],
)
def test_regression_non_ascii_digits_are_not_a_routing_number(routing: str) -> None:
    """Regression: str.isdigit() accepted Bengali / full-width / superscript
    digits, letting a non-ASCII routing number into the ASCII bank file."""
    assert routing.isdigit()
    assert pe.validate_routing_number(routing) is False
    with pytest.raises(ValueError, match="Invalid beneficiary routing number"):
        pe.generate_beftn_batch_file(_header(), [_entry(routing_number=routing)], CREATED)


# ---------------------------------------------------------------------------
# Fixed-width field formatter
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("args", "kwargs", "expected"),
    [
        (("ABC", 6), {}, "ABC   "),
        (("ABCDEFGH", 4), {}, "ABCD"),  # truncated to the field width
        (("42", 7), {"align": "right", "pad_char": "0"}, "0000042"),
        ((42, 5), {"align": "right"}, "   42"),  # non-str values are stringified
        (("", 3), {}, "   "),
    ],
)
def test_format_field(args: tuple[object, int], kwargs: dict[str, str], expected: str) -> None:
    assert beftn.format_field(*args, **kwargs) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", ["রহিম", "CAFÉ", "A\r\nB", "TAB\tX", "NUL\x00"])
def test_format_field_rejects_non_printable_ascii(bad: str) -> None:
    with pytest.raises(ValueError, match="printable ASCII"):
        beftn.format_field(bad, 22)


def test_format_field_ignores_characters_beyond_the_width() -> None:
    assert beftn.format_field("RAHIMর", 5) == "RAHIM"


# ---------------------------------------------------------------------------
# The 128-byte file, record by record
# ---------------------------------------------------------------------------


def test_file_is_six_crlf_terminated_128_byte_ascii_records() -> None:
    content = pe.generate_beftn_batch_file(_header(), _two_entries(), created_at=CREATED)
    lines = _lines(content)
    assert [line[0] for line in lines] == ["1", "5", "6", "6", "8", "9"]
    for line in lines:
        assert len(line.encode("ascii")) == 128


def test_file_header_record() -> None:
    rec = _lines(pe.generate_beftn_batch_file(_header(), _two_entries(), created_at=CREATED))[0]
    assert rec[0] == "1"
    assert rec[1:3] == "01"  # priority
    assert rec[3:13] == "BBANK     "  # immediate destination
    assert rec[13:23] == ORIGIN + " "  # immediate origin
    assert rec[23:29] == "261001"  # creation date YYMMDD
    assert rec[29:33] == "1105"  # creation time HHMM
    assert rec[33] == "A"  # file id modifier
    assert rec[34:37] == "128"  # record size
    assert rec[37:39] == "10"  # blocking factor
    assert rec[39] == "1"  # format code
    assert rec[40:63] == "BANGLADESH BANK".ljust(23)
    assert rec[63:86] == "1000 FIX SERVICES".ljust(23)
    assert rec[86:94] == "SALARY  "
    assert rec[94:] == " " * 34


def test_batch_header_record() -> None:
    rec = _lines(
        pe.generate_beftn_batch_file(
            _header(company_name="1000FIX SERVICES LIMITED BD", description="SELLER_PAYOUT"),
            _two_entries(),
            created_at=CREATED,
        )
    )[1]
    assert rec[0] == "5"
    assert rec[1:4] == "220"  # credits only
    assert rec[4:20] == "1000FIX SERVICES"  # company name truncated to 16
    assert rec[20:40] == " " * 20
    assert rec[40:50] == "COMP001   "
    assert rec[50:53] == "PPD"
    assert rec[53:63] == "SELLER_PAY"  # entry description truncated to 10
    assert rec[63:69] == "261001"
    assert rec[69:75] == "261004"  # effective (settlement) date
    assert rec[75:78] == "   "
    assert rec[78] == "1"
    assert rec[79:87] == ORIGIN[:8]
    assert rec[87:94] == "0000042"  # batch number
    assert rec[94:] == " " * 34


def test_entry_detail_records() -> None:
    lines = _lines(pe.generate_beftn_batch_file(_header(), _two_entries(), created_at=CREATED))
    first, second = lines[2], lines[3]
    assert first[0] == "6"
    assert first[1:3] == "22"  # demand credit
    assert first[3:11] == "08526123"  # RDFI routing
    assert first[11] == "4"  # check digit
    assert first[12:29] == "1051234567890".ljust(17)
    assert first[29:39] == "0004500050"  # BDT 45,000.50 in paisa
    assert first[39:54] == "EMP-001".ljust(15)
    assert first[54:76] == "RAHIM UDDIN".ljust(22)
    assert first[76:78] == "  "
    assert first[78] == "0"  # no addenda
    assert first[79:94] == ORIGIN[:8] + "0000001"  # trace number
    assert first[94:] == " " * 34
    assert second[29:39] == "0005200000"
    assert second[79:94] == ORIGIN[:8] + "0000002"


def test_batch_and_file_control_totals() -> None:
    lines = _lines(pe.generate_beftn_batch_file(_header(), _two_entries(), created_at=CREATED))
    batch_ctl, file_ctl = lines[4], lines[5]
    # entry hash = 08526123 + 09527123 = 18,053,246
    assert batch_ctl[0] == "8"
    assert batch_ctl[1:4] == "220"
    assert batch_ctl[4:10] == "000002"  # entry count
    assert batch_ctl[10:20] == "0018053246"
    assert batch_ctl[20:32] == "0" * 12  # total debit
    assert batch_ctl[32:44] == "000009700050"  # total credit (paisa)
    assert batch_ctl[44:54] == "COMP001   "
    assert batch_ctl[54:79] == " " * 25
    assert batch_ctl[79:87] == ORIGIN[:8]
    assert batch_ctl[87:94] == "0000042"
    assert file_ctl[0] == "9"
    assert file_ctl[1:7] == "000001"  # batch count
    assert file_ctl[7:13] == "000001"  # block count (6 records)
    assert file_ctl[13:21] == "00000002"
    assert file_ctl[21:31] == "0018053246"
    assert file_ctl[31:43] == "0" * 12
    assert file_ctl[43:55] == "000009700050"
    assert file_ctl[55:] == " " * 73


@pytest.mark.parametrize(("n_entries", "blocks"), [(1, "000001"), (6, "000001"), (7, "000002")])
def test_block_count_is_records_over_ten_rounded_up(n_entries: int, blocks: str) -> None:
    entries = [_entry(employee_id=f"E{i}", amount_bdt=D("1.00")) for i in range(n_entries)]
    lines = _lines(pe.generate_beftn_batch_file(_header(), entries, created_at=CREATED))
    assert len(lines) == n_entries + 4
    assert lines[-1][7:13] == blocks


def test_entry_hash_keeps_the_low_order_ten_digits() -> None:
    entries = [
        _entry(employee_id=f"E{i:03d}", routing_number="999999999", amount_bdt=D("1.00"))
        for i in range(101)
    ]
    lines = _lines(pe.generate_beftn_batch_file(_header(), entries, created_at=CREATED))
    # 99,999,999 x 101 = 10,099,999,899 -> last ten digits
    assert lines[-2][10:20] == "0099999899"
    assert lines[-1][21:31] == "0099999899"
    assert lines[-2][4:10] == "000101"
    assert lines[-2][32:44] == "000000010100"


def test_creation_stamp_defaults_to_now(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2027, 1, 3, 9, 7)

    monkeypatch.setattr(beftn, "datetime", _FrozenDatetime)
    rec = _lines(pe.generate_beftn_batch_file(_header(), _two_entries()))[0]
    assert rec[23:33] == "2701030907"


def test_whole_paisa_amount_with_trailing_zero_is_accepted() -> None:
    lines = _lines(
        pe.generate_beftn_batch_file(_header(), [_entry(amount_bdt=D("45000.500"))], CREATED)
    )
    assert lines[2][29:39] == "0004500050"


def test_largest_representable_entry_amount() -> None:
    lines = _lines(
        pe.generate_beftn_batch_file(_header(), [_entry(amount_bdt=D("99999999.99"))], CREATED)
    )
    assert lines[2][29:39] == "9999999999"
    assert lines[-1][43:55] == "009999999999"


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


def test_invalid_originating_routing_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid originating routing number: INVALID"):
        pe.generate_beftn_batch_file(_header(originating_routing="INVALID"), _two_entries())


def test_empty_entry_list_rejected() -> None:
    with pytest.raises(ValueError, match="empty entries list"):
        pe.generate_beftn_batch_file(_header(), [])


def test_invalid_beneficiary_routing_names_the_employee() -> None:
    with pytest.raises(ValueError, match="BADROUT for EMP-009"):
        pe.generate_beftn_batch_file(
            _header(), [_entry(employee_id="EMP-009", routing_number="BADROUT")], CREATED
        )


@pytest.mark.parametrize("amount", [D("0"), D("-0.01"), D("-100")])
def test_non_positive_amount_rejected(amount: Decimal) -> None:
    with pytest.raises(ValueError, match="Amount must be positive"):
        pe.generate_beftn_batch_file(_header(), [_entry(amount_bdt=amount)], CREATED)


@pytest.mark.parametrize("amount", [D("0.004"), D("0.005"), D("100.125"), D("1.001")])
def test_regression_sub_paisa_amount_rejected_not_rounded(amount: Decimal) -> None:
    """Regression: amounts were converted with the context's half-even
    rounding, so 0.004 became a zero-paisa credit line (bypassing the
    positive-amount guard) and 100.125 lost half a paisa against the
    half-up ledger. A bank instruction must be an exact paisa amount."""
    with pytest.raises(ValueError, match="whole number of paisa"):
        pe.generate_beftn_batch_file(_header(), [_entry(amount_bdt=amount)], CREATED)


def test_regression_amount_overflowing_the_entry_field_rejected() -> None:
    """Regression: BDT 100,000,000.00 = 10,000,000,000 paisa (11 digits) was
    silently cut to the leftmost 10 digits ('1000000000' = BDT 10,000,000),
    instructing the bank to pay a tenth of the amount."""
    with pytest.raises(ValueError, match="10-digit BEFTN amount field"):
        pe.generate_beftn_batch_file(_header(), [_entry(amount_bdt=D("100000000.00"))], CREATED)


def test_regression_batch_total_overflowing_the_control_field_rejected() -> None:
    """Regression: a total credit above 12 digits of paisa was silently
    truncated in the batch/file control records."""
    entries = [_entry(employee_id=f"E{i:03d}", amount_bdt=D("99999999.99")) for i in range(101)]
    with pytest.raises(ValueError, match="12-digit BEFTN total field"):
        pe.generate_beftn_batch_file(_header(), entries, CREATED)


@pytest.mark.parametrize(
    "overrides",
    [
        {"employee_name": "রহিম উদ্দিন"},
        {"employee_name": "RAHIM\r\n6220000"},
        {"account_number": "১০৫১"},
        {"employee_id": "EMP\t001"},
    ],
)
def test_regression_non_ascii_or_control_text_rejected(overrides: dict[str, str]) -> None:
    """Regression: a Bengali name became a multi-byte (>128-byte) record and
    an embedded CR/LF split a record in two; both now fail loudly."""
    with pytest.raises(ValueError, match="printable ASCII"):
        pe.generate_beftn_batch_file(_header(), [_entry(**overrides)], CREATED)


def test_regression_non_ascii_company_name_rejected() -> None:
    with pytest.raises(ValueError, match="printable ASCII"):
        pe.generate_beftn_batch_file(
            _header(company_name="১০০০ ফিক্স"),
            _two_entries(),
            CREATED,
        )
