# msp_periods — the M05 reporting month as a Bangladesh business month
# (A02 ERP audit M05-F15). Not a model file: imported directly, like msp_roles.
#
# The monthly report and the credit run built their periods from naive
# dates combined with midnight, which the ORM reads as UTC: an alert raised
# on the 1st before 06:00 Dhaka time fell into the previous month, and one
# raised on the last day after 18:00 into the next. The business day is
# Asia/Dhaka (UTC+6): a period is that calendar month, converted to UTC.
import re
from datetime import datetime, time, timedelta

import pytz

BD_TZ = pytz.timezone("Asia/Dhaka")
# the one spelling of a reporting month: a free-text label made two credits of
# one month ("2026-1" beside "2026-01"; A02 pass-2 review P2)
PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def dhaka_today():
    """Today's date in Dhaka, whatever the server or cron user's zone."""
    return datetime.now(BD_TZ).date()


def dhaka_date(stamp):
    """The Dhaka calendar date of a naive-UTC datetime (a date is returned
    as it is; None is None)."""
    if not stamp:
        return None
    if isinstance(stamp, datetime):
        return pytz.utc.localize(stamp).astimezone(BD_TZ).date()
    return stamp


def _utc(day, end):
    local = datetime.combine(day, time.max if end else time.min)
    return BD_TZ.localize(local).astimezone(pytz.utc).replace(tzinfo=None)


def dhaka_month(day):
    """(utc_start, utc_end, 'YYYY-MM') of the Dhaka calendar month of ``day``."""
    first = day.replace(day=1)
    last = (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return _utc(first, False), _utc(last, True), first.strftime("%Y-%m")


def dhaka_previous_month(today=None):
    """The Dhaka calendar month before the one ``today`` (Dhaka) falls in."""
    today = today or dhaka_today()
    return dhaka_month(today.replace(day=1) - timedelta(days=1))


def month_dates(label):
    """(first, last) dates of a 'YYYY-MM' period label, or (None, None)."""
    try:
        first = datetime.strptime(str(label or "").strip(), "%Y-%m").date()
    except ValueError:
        return None, None
    return first, (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
