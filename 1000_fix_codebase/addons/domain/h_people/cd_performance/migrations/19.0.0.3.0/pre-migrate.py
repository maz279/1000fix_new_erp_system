# cd_performance 19.0.0.3.0 — the incentive run's 'applied' state is gone (A09
# I4: M57 no longer writes payslips; a run is approved, then payroll picks its
# lines up). A run that was 'applied' was never approved by anyone, so it goes
# back to 'computed' and must be routed for approval like any other.


def migrate(cr, version):
    cr.execute("UPDATE fix_incentive_run SET state = 'computed' WHERE state = 'applied'")
