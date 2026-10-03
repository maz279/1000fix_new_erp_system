"""reconciliation — P06-M04-T08 / P06-M05-T07 (CD-M50-nn).

The auto-matching rules engine for payment reconciliation. PURE FUNCTIONS —
no Odoo, no I/O — so the >=90% match-rate gate criterion (G3-02) is proven
by unit tests against realistic statement shapes, not hoped for in
production.

The ladder (in order, first hit wins — same ladder the Odoo-side
auto_match uses):

  R1  exact reference   — the invoice ref appears verbatim in the bank
                          reference or narration, amounts equal
  R2  amount+window     — amount equal, date within +-3 days of ONE open
                          invoice with that amount (uniqueness required)
  R3  amount+customer   — amount equal plus customer name token in the
                          narration, within +-30 days
  R4  gateway batch     — bKash/Nagad/SSLCOMMERZ settlement batch lines
                          (identified by narration prefix), matched by
                          sum-of-transactions within the settlement window

Anything unmatched falls to manual review — never guessed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

WINDOW_DAYS_EXACT = 3
WINDOW_DAYS_LOOSE = 30
GATEWAY_PREFIXES = ("BKASH", "NAGAD", "SSLC", "SSLCOMMERZ")
TARGET_MATCH_RATE = 90  # G3-02, percent


@dataclass(frozen=True)
class OpenItem:
    """An unpaid invoice awaiting settlement."""
    ref: str
    customer: str
    amount: Decimal
    due_date: date


@dataclass(frozen=True)
class StatementLine:
    date: date
    amount: Decimal
    reference: str = ""
    narration: str = ""


@dataclass
class Match:
    line_index: int
    rule: str          # R1..R4 | manual
    item_ref: str
    detail: str = ""


@dataclass
class ReconResult:
    matches: list[Match] = field(default_factory=list)
    manual: list[int] = field(default_factory=list)
    match_rate: float = 0.0

    @property
    def meets_gate(self) -> bool:
        return self.match_rate >= TARGET_MATCH_RATE


def _amount_eq(a: Decimal, b: Decimal) -> bool:
    return a == b  # both already 2dp-quantised by the feed


def _within(line_date: date, item_date: date, days: int) -> bool:
    return abs((line_date - item_date).days) <= days


def reconcile(lines: list[StatementLine], items: list[OpenItem]) -> ReconResult:
    """Match statement lines against open items. Each item matches at most
    once (an invoice is settled once); each line matches at most once."""
    result = ReconResult()
    taken: set[str] = set()

    def find(rule: str, predicate) -> Match | None:
        for item in items:
            if item.ref in taken:
                continue
            if predicate(item):
                return Match(line_index, rule, item.ref)
        return None

    for line_index, line in enumerate(lines):
        upper_ref = (line.reference or "").upper()
        narration = (line.narration or "").upper()
        match = None

        if any(upper_ref.startswith(p) or narration.startswith(p) for p in GATEWAY_PREFIXES):
            # R4: settlement batches — sum of open items equal to the batch
            batch_sum = sum((i.amount for i in items if i.ref not in taken), Decimal("0"))
            if _amount_eq(batch_sum, line.amount):
                for item in items:
                    if item.ref not in taken and _within(line.date, item.due_date, WINDOW_DAYS_LOOSE):
                        match = Match(line_index, "R4", item.ref,
                                      detail="gateway settlement batch")
                        break
        if match is None:
            match = find("R1", lambda it: (
                _amount_eq(it.amount, line.amount)
                and (it.ref.upper() in upper_ref or it.ref.upper() in narration)))
        if match is None:
            candidates = [
                it for it in items
                if it.ref not in taken and _amount_eq(it.amount, line.amount)
                and _within(line.date, it.due_date, WINDOW_DAYS_EXACT)
            ]
            if len(candidates) == 1:  # uniqueness — ambiguity goes to manual
                match = Match(line_index, "R2", candidates[0].ref)
        if match is None:
            tokens = {t for t in narration.split() if len(t) >= 4}
            match = find("R3", lambda it: (
                _amount_eq(it.amount, line.amount)
                and _within(line.date, it.due_date, WINDOW_DAYS_LOOSE)
                and any(tok in it.customer.upper() for tok in tokens)))

        if match:
            result.matches.append(match)
            taken.add(match.item_ref)
        else:
            result.manual.append(line_index)

    total = len(lines)
    result.match_rate = round(100.0 * len(result.matches) / total, 2) if total else 100.0
    return result


def main() -> None:
    """Smoke: a realistic day — gateway batch, three R1s, one ambiguous."""
    today = date(2026, 10, 2)
    items = [
        OpenItem("AR/101", "Rahim Uddin", Decimal("1150.00"), today - timedelta(days=2)),
        OpenItem("AR/102", "Karim Traders", Decimal("2300.00"), today - timedelta(days=1)),
        OpenItem("AR/103", "Rahim Uddin", Decimal("1150.00"), today - timedelta(days=20)),
    ]
    lines = [
        StatementLine(today, Decimal("1150.00"), reference="AR/101 CREDIT"),
        StatementLine(today, Decimal("2300.00"), narration="NEFT KARIM TRADERS"),
        StatementLine(today, Decimal("3450.00"), reference="BKASH BATCH 88"),
        StatementLine(today, Decimal("99.00"), narration="BANK CHARGE"),
    ]
    result = reconcile(lines, items)
    print(f"matched={len(result.matches)} manual={result.manual} rate={result.match_rate}% "
          f"gate={'PASS' if result.meets_gate else 'FAIL'}")


if __name__ == "__main__":
    main()
