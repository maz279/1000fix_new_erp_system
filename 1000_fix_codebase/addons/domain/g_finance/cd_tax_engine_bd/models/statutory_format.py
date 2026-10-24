"""statutory_format — BN-007 amount presentation for the statutory forms.

PURE functions (no Odoo imports), used by the Mushak 6.6 and income-tax
withholding-certificate reports so the amounts printed on a statutory form
are formatted by the backend, never by the template:

  * format_bdt()      — BN-007: the currency sign BEFORE the amount, a thin
                        space, two decimals rounded half-up, lakh-crore
                        grouping (1,23,45,678.90), the minus sign before the
                        symbol; Bengali numerals in the "bn" locale.
  * amount_in_words() — the amount in words for the "in words" line of the
                        forms (DT-013 §3: figures AND words), lakh-crore
                        wording in Arabic-numeral-free English (FM-13-d).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from num2words import num2words

TWO = Decimal("0.01")
THIN_SPACE = " "
_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn_numerals(text: str) -> str:
    """Arabic digits -> Bengali digits (identifiers are never converted)."""
    return str(text).translate(_BN_DIGITS)


def group_lakh(whole: str) -> str:
    """'12345678' -> '1,23,45,678' (last three digits, then pairs)."""
    if len(whole) <= 3:
        return whole
    head, last3 = whole[:-3], whole[-3:]
    pairs = []
    while len(head) > 2:
        pairs.insert(0, head[-2:])
        head = head[:-2]
    pairs.insert(0, head)
    return ",".join(pairs) + "," + last3


def _quantized(amount) -> Decimal:
    return Decimal(str(amount or 0)).quantize(TWO, ROUND_HALF_UP)


def format_bdt(amount, locale: str = "en") -> str:
    """BN-007 amount string: 'BDT 1,50,000.00' / '৳ ১,৫০,০০০.০০'."""
    value = _quantized(amount)
    whole, frac = f"{abs(value):.2f}".split(".")
    body = f"{group_lakh(whole)}.{frac}"
    sign = "-" if value < 0 else ""
    if locale == "bn":
        return f"{sign}৳{THIN_SPACE}{bn_numerals(body)}"
    return f"{sign}BDT{THIN_SPACE}{body}"


def format_rate(rate) -> str:
    """A statutory rate to three decimals (DT-013 §4: '%, 3 dp'): '15.000%'."""
    return f"{Decimal(str(rate or 0)).quantize(Decimal('0.001'), ROUND_HALF_UP)}%"


def amount_in_words(amount) -> str:
    """'Taka One Lakh Fifty Thousand and Poisha Fifty Only' (BDT, lakh-crore)."""
    value = _quantized(amount)
    if value < 0:
        raise ValueError("a certified amount cannot be negative")
    taka = int(value)
    poisha = int((value - taka) * 100)
    words = "Taka " + num2words(taka, lang="en_IN").replace(",", "").title()
    if poisha:
        words += " and Poisha " + num2words(poisha, lang="en_IN").title()
    return words.replace(" And ", " and ") + " Only"
