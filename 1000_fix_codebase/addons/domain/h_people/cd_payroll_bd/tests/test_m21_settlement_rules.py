# M21 bidirectional audit (13 Nov 2026): the settlement figures the exit
# types produced against BLA 2006. Pure functions: no database needed.
from datetime import date

from odoo.addons.cd_payroll_bd.models.fix_payroll_statutory import separation_figures

JOIN, LAST = date(2021, 3, 1), date(2026, 3, 1)  # 5 completed years, basic 30,000 = 1,000/day


def _lines(*args, **kw):
    _y, lines = separation_figures(30000.0, JOIN, LAST, *args, **kw)
    return {k: float(a) for k, _l, a in lines}


def test_a_dismissal_pays_its_earned_leave_and_raises_nothing():
    """E1: 'No settlement rule is defined for exit type dismissal' - a
    dismissed worker was never paid even the s.11 earned leave."""
    assert _lines("dismissal") == {}
    assert _lines("dismissal", unused_leave_days=6.0) == {"leave_encashment": 6000.0}


def test_termination_notice_follows_the_workers_status():
    """E3: 120 days in lieu was paid to a temporary worker owed 30 (s.26(2)),
    and the s.26(4) compensation is a permanent worker's."""
    temp = _lines("termination", notice_required_days=30, permanent=False)
    assert temp["notice_pay"] == 30000.0 and "service_compensation" not in temp
    perm = _lines("termination", notice_required_days=120, permanent=True)
    assert perm["notice_pay"] == 120000.0
    assert perm.get("service_compensation", perm.get("gratuity")) >= 150000.0
    # notice served is netted off
    served = _lines("termination", notice_required_days=30, permanent=False, notice_served_days=30)
    assert "notice_pay" not in served


def test_a_resignation_short_of_notice_pays_wages_in_lieu():
    """E4: s.27(3) - the treatment 'Wages in Lieu of Notice' was never read."""
    lines = _lines("resignation", shortfall_recovery_days=20)
    assert lines["notice_recovery"] == -20000.0
    assert "notice_recovery" not in _lines("resignation")
