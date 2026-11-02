"""payroll-engine — P08-M03 / R06-M03 (CD-M56-01; TSS §20.2 W5; DoD-03).

The L5 service shell for the Bangladesh payroll calculation kernel. The
kernel itself lives in libs/py/payroll_engine (shared kernel: reachable
from the Odoo module at runtime via the same libs.py.* path that the
outbox uses, from pytest, and from here). This shell is the service's
public contract and version anchor; the exhaustive DoD-03 test suite
(100% of every payroll calculation path — payroll is the
highest-consequence financial path in the estate) lives in tests/.

Re-exports the kernel so consumers depend on the service, not the path.
"""

from libs.py.payroll_engine import (
    GRATUITY_DAYS_ABOVE_12Y,
    GRATUITY_DAYS_UPTO_12Y,
    GRATUITY_MIN_YEARS_VESTING,
    MINIMUM_TAX_LOCATIONS,
    OT_BASE_COMPONENTS,
    OT_DIVISOR_HOURS,
    RESIGNATION_BANDS,
    SALARY_EXEMPTION_CEILING,
    STANDARD_DAY_HOURS,
    TAX_FREE_THRESHOLD,
    TAX_FREE_THRESHOLDS,
    TAX_SLABS,
    BeftnBatchHeader,
    BeftnEntry,
    PayslipInput,
    PayslipResult,
    beftn_settlement_date,
    completed_years,
    compute_payslip,
    generate_beftn_batch_file,
    gratuity,
    income_tax,
    investment_tax_rebate,
    is_pf_deposit_compliant,
    is_working_day,
    overtime_amount,
    provident_fund,
    q2,
    resignation_compensation,
    retrenchment_compensation,
    salary_exemption,
    validate_routing_number,
)

__all__ = [
    "GRATUITY_DAYS_ABOVE_12Y",
    "GRATUITY_DAYS_UPTO_12Y",
    "GRATUITY_MIN_YEARS_VESTING",
    "MINIMUM_TAX_LOCATIONS",
    "OT_BASE_COMPONENTS",
    "OT_DIVISOR_HOURS",
    "RESIGNATION_BANDS",
    "SALARY_EXEMPTION_CEILING",
    "STANDARD_DAY_HOURS",
    "TAX_FREE_THRESHOLD",
    "TAX_FREE_THRESHOLDS",
    "TAX_SLABS",
    "BeftnBatchHeader",
    "BeftnEntry",
    "PayslipInput",
    "PayslipResult",
    "beftn_settlement_date",
    "completed_years",
    "compute_payslip",
    "generate_beftn_batch_file",
    "gratuity",
    "income_tax",
    "investment_tax_rebate",
    "is_pf_deposit_compliant",
    "is_working_day",
    "overtime_amount",
    "provident_fund",
    "q2",
    "resignation_compensation",
    "retrenchment_compensation",
    "salary_exemption",
    "validate_routing_number",
]
