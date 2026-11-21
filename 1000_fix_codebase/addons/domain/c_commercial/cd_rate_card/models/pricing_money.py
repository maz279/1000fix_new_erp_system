# The one M11 money rounding (A04 ERP audit 20 Nov 2026, M11-F16).
#
# Rounding was HALF_EVEN in the dynamic rule, HALF_UP in the parts scheme and
# Python's float round() in promotions, so 1.545 became 1.54 on one screen and
# 1.55 on another. Every M11 price now rounds through money(): half-up, in
# Decimal, to the paisa unless a coarser step (FR-PRC-008 whole-taka rounding)
# is asked for.
from decimal import ROUND_HALF_UP, Decimal


def money(value, step=0.01) -> float:
    """Round half-up to `step` (0.01 = the paisa; 1, 5, 10 = whole taka)."""
    step = Decimal(str(step or 0.01))
    units = (Decimal(str(value or 0.0)) / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return float(units * step)
