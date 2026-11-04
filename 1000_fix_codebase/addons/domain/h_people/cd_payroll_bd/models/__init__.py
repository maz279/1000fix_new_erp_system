# ruff: noqa: I001
# cd_payroll_bd models. Load order: the statutory settings and the exit
# settlement hook first, then the payroll documents that use them.
from . import (
    res_users_payroll,
    fix_payroll_statutory,
    fix_payroll_settlement,
    fix_payroll,
    fix_payroll_ops,
)
